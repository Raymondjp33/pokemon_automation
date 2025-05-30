// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stream_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StreamData _$StreamDataFromJson(Map<String, dynamic> json) => StreamData(
      switch1CurrentlyHunting: json['switch1_currently_hunting'] as String,
      switch2CurrentlyHunting: json['switch2_currently_hunting'] as String,
      away: json['away'] as bool,
      streamStarttime: json['stream_starttime'] as num,
      switch1GifNumber: json['switch1_gif_number'] as String,
      switch2GifNumber: json['switch2_gif_number'] as String,
      switch1Target: (json['switch1_target'] as num?)?.toInt(),
      switch2Target: (json['switch2_target'] as num?)?.toInt(),
      switch2Targets: (json['switch2_targets'] as List<dynamic>?)
              ?.map((e) => TargetModel.fromJson(e as Map<String, dynamic>?))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$StreamDataToJson(StreamData instance) =>
    <String, dynamic>{
      'switch1_currently_hunting': instance.switch1CurrentlyHunting,
      'switch2_currently_hunting': instance.switch2CurrentlyHunting,
      'away': instance.away,
      'stream_starttime': instance.streamStarttime,
      'switch1_gif_number': instance.switch1GifNumber,
      'switch2_gif_number': instance.switch2GifNumber,
      'switch1_target': instance.switch1Target,
      'switch2_target': instance.switch2Target,
      'switch2_targets':
          instance.switch2Targets.map((e) => e.toJson()).toList(),
    };
